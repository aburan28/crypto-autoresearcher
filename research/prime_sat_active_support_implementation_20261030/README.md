# Cold active-support refutation

`refute_active` keeps the frozen selected-row polynomial-calculus kernel and iterates over the increasing original indices appearing in all cleaned input generators. Validation and eager support extraction are outside that kernel. The original generator order, variable labels, pivot policy, FIFO queue, insertion cap and certificate arithmetic are retained.

The source implication is recorded in DEC-20261030-722a2d. Its premises include prime p, frozen Boolean-quotient arithmetic and cold inputs. Input validation checks canonical integer types and mask bounds; it does not certify primality. A baseline refutation must retain its exact ordered multiplier certificate within the same insertion cap. UNKNOWN retains the original selected-strategy meaning.

`checked_refute("baseline", ...)` calls the original refuter after the same input validation. `engine_bridge.solve(..., refuter_mode=...)` loads a fresh private engine namespace and changes only its private `legacy.refute` binding. Existing callback, proof-check, model-blocking and projected-cover logic is reused. The original return fields stay intact; `refuter_diagnostics` adds per-call validation/support events and original active indices. These different event units are recorded separately. Support scans include generators the baseline might never reach.

The frozen software contract is `coordination/prime_sat_active_support_implementation_20261030/software-contract.json`: 14 cold fixtures, malformed/source and direct callback controls, and 24 native F5 slots (four existing families, two refuter modes, three callback strategies). Each native slot has a 5-second watchdog; a suite has a 180-second watchdog and a 2 GiB address-space limit. Each actor has at most four suite attempts. `producer-results.json` retains each attempted source revision, command, assertion, transcript, failure, and source hash. The independent reviewer authors its own harness.

Run the admitted producer suite from the repository root:

```sh
/home/ec2-user/prime-sat-research-venv/bin/python -B research/prime_sat_active_support_implementation_20261030/test_active_support.py --receipt research/prime_sat_active_support_implementation_20261030/producer-results.json
```

Implementation is present; execution status is recorded only in the actual receipt. `run_cell` is provided for the subsequent separately specified four-encoding comparison and is not invoked by this fixed suite. That comparison must include eager setup and reconstruction/checking costs alongside search work.
