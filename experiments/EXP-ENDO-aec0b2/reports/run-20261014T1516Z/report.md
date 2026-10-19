# Transport Denominators: deterministic pilot observations

## Observation-only status

This report records execution outputs; it makes no support, weakening, priority or scientific-status decision. Independent mathematical review remains separate. All instances are supplied synthetic lattices.

## Trial and provenance

Experiment EXP-ENDO-aec0b2; hypothesis H-ENDO-3ecfa3; run RUN-ENDO-4d758c. Code commit d912095ca32542b251e17aec71c7124a42237cfb. Seed 1729. Exact command: ["python3", "tools/lattice_transport_denominators.py", "--seed", "1729", "--output-dir", "/workspace/lattice-transport/experiments/EXP-ENDO-aec0b2/runs/RUN-ENDO-4d758c"]. One trial requested; completion/failure and resource observations are preserved in execution-receipt.json. The driver records full-tree dirtiness as unknown when not supplied; every source byte is admitted against its committed hash.

## Recorded outputs

Exact fixture counters (integer counts, not independent statistical samples): {"all_exact_checks_passed": true, "basis_cases": 17280, "changed_lattice_denominator_arms": 3956, "generator_arms": 3456, "nonprimitive_concealment_arms": 656, "ordered_pair_cases": 1152}. Supervisor receipt: {"artifact_sha256": {"check.stderr.log": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", "check.stdout.log": "af8e9a371091dd2327af3784f48f79d137de7e7e00403d323475183ee8867f36", "command.txt": "87c700d8cfacf17e7d8de3a374e43694d8e75b433a73e208764d34eaaa8304b2", "environment.json": "39bd0b998519e671969cdc3c06732a839166643efcddb4ce3c76f3c76d4a51a7", "launch.json": "72cfed452c3e44951bba7feb6c4844abbf700c9cc643ae705b0cbcd146ca46bf", "manifest.yaml": "1b649202da7b29d9efbc19c82eb2c9efb511e798be164208ca3093cc9725d24d", "raw-result.json": "8652de0792a15a569ff057085fe5bbc408cbe2772e24005c6351a9e8149ee1bb", "stderr.log": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", "stdout.log": "e96a6d36b01c687ab83222276b16df61f00663646f3fb2b738ec3b2b4ba19570"}, "authority": {"commit": "d912095ca32542b251e17aec71c7124a42237cfb", "dispatch_plan_sha256": "c2fcc3e07af4b9990cfdb0c5ead30c69350492cba1911aff51d322d12df1155a", "epoch": 1, "expires_at": "2026-10-14T16:13:16+00:00", "owner": "lattice-executor-20261014"}, "check_returncode": 0, "detail": null, "finished_at": "2026-10-14T15:16:47.474269+00:00", "plan_sha256": "4ae72b511cd82658c0e72c461db2d1b1e0b0a0ebcf8cdf0dd593dbd3e8bcd6f3", "published": false, "returncode": 0, "run_id": "RUN-ENDO-4d758c", "schema": "crypto.autoresearch.trial_receipt.v1", "scientific_conclusion": null, "started_at": "2026-10-14T15:16:39.724542+00:00", "status": "output_validated", "trial_id": "exact-pilot-seed1729"}

## Control scope and graph

One retained ordered pair D_K=-4, f_i=1, f_j=6; three generator scales. All plotted values come directly from raw-result.json; no new sampling is performed. Uncertainty bars are inapplicable to these deterministic exact values. Plot source and extracted data are retained.

## Limitations and missing data

Supplied C/O_f principal lattices and known generators, not unknown finite-field rings. Nonunimodular target changes can alter the order; original conductor formulas are not applied to them. Nonprimitive generators can conceal conductor differences; an anchor is required for absolute scale. Faithful synthetic modules are not a substitute for realizing geometric torsion or actual finite-field maps. No map-discovery cost, practical speedup, ECDLP consequence or characteristic-prime division was measured. The integrity checker replays the implementation; it is not independent research review. No ECDLP canonical graph or frontier was changed.

[Recorded-value plot](observations.svg) · [PDF](report.pdf)
