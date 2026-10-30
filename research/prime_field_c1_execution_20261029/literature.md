# C1 execution-contract source review

29 October 2026, `/root/c1_execution_contract`. This review prepared administrative
source/protocol bindings only; no fixed P-256 case was imported or executed.

- **Retrieved primary:** Petit, Kosters and Messeng, *Algebraic approaches for
  the Elliptic Curve Discrete Logarithm Problem over prime fields*, PKC 2016,
  https://people.maths.ox.ac.uk/petit/files/16PKC_primeECDLP.pdf. The retained
  primary PDF `/workspace/pkm-prime-fields.pdf` was opened directly. Page 8,
  section 3.2, states separate relation-solver and linear-algebra costs and the
  unresolved solver threshold. Section 3.3 describes subgroup/coset membership
  constructions. An exact small representation or successful extraction is
  not a total attack-cost or asymptotic improvement claim.
- **Internal original sources:** `research/p256_factor_base_parallel_20261026/`
  `workflow/execution-gates.md`, F1 `literature.md`, `report.md`, `core.py`,
  `exterior.py`, `driver.py`, `profiled.py`, `reference.py`, `inputs.json` and
  the shared `runtime/checkpoint_gate.py`. The original seven cases, all three
  multiplicity strata, finite oracle, 560 guard and no-overwrite semantics
  remain unchanged. Source, frozen protocol, actual checkpoint and explicit
  root release are the original Phase B requirements, not new user approvals.
- **Internal administrative references:** `docs/experiment-protocol.md`, both
  protocol/export schemas and `tools/experiment_protocol.py`; the existing
  F3 protocol/export pattern distinguishes method cells sharing one physical
  process. The new contract follows that pattern without importing F3 data or
  claims. Exact counts describe completed fixed cases only.
- **Operational observation:** the committed checkpoint upload receipt records
  a real gate success and authenticated archive readback. It proves that
  session's transport, not persistent credentials or execution approval.
- **Model readiness:** `model-readiness.txt` retains the actual configured
  adapter probe: `ANTHROPIC_API_KEY` is unset and the configured model IDs are
  unverified. No model verification, independent scientific review, official
  hypothesis/goal transition or backend substitution is claimed here.

The exterior construction's priority and scalable performance are outside this
contract. No broader literature completeness or novelty claim is made.
