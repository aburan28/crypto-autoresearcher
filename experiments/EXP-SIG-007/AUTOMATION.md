
## Addendum 2026-07-26
- Use `fire_budget: 2700` (not 3300): with ~450 s basis load, 3300 lets the last unit run past the 3600 s runtime timeout (observed: run killed mid-unit at 3600 s; completed units were safe via per-unit checkpointing).
- Blueprint runtime nests `runInput` under a top-level `input` key in the injected env config; runner >= 2026-07-26 merges it (patch confirmed live).
- One automation = one active run. Parallel control directions use the second automation `automation_707000ac-91a7-41dc-8bd8-34ad4a300a2a` (entry via absolute path).
- The adapter may report "no result within 1800000ms" on Automation.run while the run actually launches — always verify via listRuns before retrying (duplicate triggers are skipped safely).
