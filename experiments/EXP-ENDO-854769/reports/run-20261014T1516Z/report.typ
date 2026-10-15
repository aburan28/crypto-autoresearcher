#set page(paper: "a4", margin: 18mm)
#set text(size: 10pt)
#set par(justify: false)
= Order Saturation: deterministic pilot observations
== Observation-only status
#text("This report records execution outputs; it makes no support, weakening, priority or scientific-status decision. Independent mathematical review remains separate. All instances are supplied synthetic lattices.")

== Trial and provenance
#text("Experiment EXP-ENDO-854769; hypothesis H-ENDO-ccf484; run RUN-ENDO-910c24. Code commit 1e4fd5c77cf9f4ef7337ad0a9f29568174538a4b. Seed 1729. Exact command: [\"python3\", \"tools/lattice_order_saturation.py\", \"--seed\", \"1729\", \"--output-dir\", \"/workspace/lattice-saturation/experiments/EXP-ENDO-854769/runs/RUN-ENDO-910c24\"]. One trial requested; completion/failure and resource observations are preserved in execution-receipt.json. The driver records full-tree dirtiness as unknown when not supplied; every source byte is admitted against its committed hash.")

== Recorded outputs
#text("Exact fixture counters (integer counts, not independent statistical samples): {\"all_exact_checks_passed\": true, \"division_controls\": 512, \"order_cases\": 32, \"policy_arms\": 64, \"wrong_ambient_collisions\": 32}. Supervisor receipt: {\"artifact_sha256\": {\"check.stderr.log\": \"e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855\", \"check.stdout.log\": \"af8e9a371091dd2327af3784f48f79d137de7e7e00403d323475183ee8867f36\", \"command.txt\": \"423866794d3f8858d9a6bb858412ade9c602dd8319a3f5fa3bb4f296325d995b\", \"environment.json\": \"162b563ecf0da84fd1101dc77f607dafb1eec2142039cb33db0c21ef887ecdb0\", \"launch.json\": \"21cd754de1c2f026cf697711a92ee24c4a645c353e286beb534f24f3d44a0f2a\", \"manifest.yaml\": \"d6278bfda20ff82d9eaf8deceafd9dee3e391987aff7965720ebc07dd639b8e3\", \"raw-result.json\": \"f906d4d05bb1ff8128a64a56892fb6067ba89bac33f12338a2012e69013adefb\", \"stderr.log\": \"e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855\", \"stdout.log\": \"4914f20c5b5e938b1b0913279de8f604da79fd9dcb5a35827f4e994cb21def48\"}, \"authority\": {\"commit\": \"1e4fd5c77cf9f4ef7337ad0a9f29568174538a4b\", \"dispatch_plan_sha256\": \"73575df19302de2c6d2669300f09b59542ebcaad73f6d2944db8504b4f35b124\", \"epoch\": 1, \"expires_at\": \"2026-10-14T16:13:16+00:00\", \"owner\": \"lattice-executor-20261014\"}, \"check_returncode\": 0, \"detail\": null, \"finished_at\": \"2026-10-14T15:16:41.276773+00:00\", \"plan_sha256\": \"173e178ec736e4d59284bac8b5385176089e9aae9770d46aea08567704bf7c5f\", \"published\": false, \"returncode\": 0, \"run_id\": \"RUN-ENDO-910c24\", \"schema\": \"crypto.autoresearch.trial_receipt.v1\", \"scientific_conclusion\": null, \"started_at\": \"2026-10-14T15:16:41.067366+00:00\", \"status\": \"output_validated\", \"trial_id\": \"exact-pilot-seed1729\"}")

== Control scope and graph
#text("One retained supplied pool. Scoring and map-acquisition costs are incomplete; this is not a speedup comparison. All plotted values come directly from raw-result.json; no new sampling is performed. Uncertainty bars are inapplicable to these deterministic exact values. Plot source and extracted data are retained.")

== Limitations and missing data
#text("The actual ambient order and candidate generators are supplied, not discovered. Selection counts omit isogeny construction/evaluation and are not performance claims. Full additive rank is not full order saturation; scalar and redundant maps are retained controls. Torsion division is certified only on the actual faithful supplied lattice. No finite-field characteristic-prime division, subgroup solve, or ECDLP consequence was measured. The integrity checker replays the implementation; it is not independent research review. No ECDLP canonical graph or frontier was changed.")

#figure(image("observations.svg", width: 100%), caption: "One retained supplied pool. Scoring and map-acquisition costs are incomplete; this is not a speedup comparison. Run RUN-ENDO-910c24.")
