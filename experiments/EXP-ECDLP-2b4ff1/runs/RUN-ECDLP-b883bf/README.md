# Retained run observations

RUN-ECDLP-b883bf / EXP-ECDLP-2b4ff1. The official supervisor completed one admitted trial, with 768/768 native children and return/check codes 0. Scientific interpretation is separate from this operational record.

The complete original controller tree is retained in `modal-evidence.tar.gz`, including all 768 native streams, per-child inputs, counters, clocks/rusage, actual provider identity, complete raw manifests, both archive layers and collection/quiescence receipts. Its content-addressed store identity is in `.artifacts.json` and `modal-evidence.tar.gz.blob.json`; actual full GET/hash readback is recorded in `artifact-readback.json`. No source credential, private target root, or withheld truth manifest entered the VM inputs or archive.

`execution-receipt.json` records the supervisor's own automatic gzip storage of the large logical `modal-evidence-manifest.json`; the stored gzip and its blob pointer retain both stored and logical hashes. The hydrated `modal/` tree and logical manifest are ignored to avoid duplicating the exact archive bytes in Git. Both remain materialized locally for all subsequent checks.

To reproduce after a fresh checkout, use the repository's normal configured artifact transport:

```sh
python3 tools/artifacts/artifacts.py pull experiments/EXP-ECDLP-2b4ff1/runs/RUN-ECDLP-b883bf
python3 tools/artifacts/artifacts.py verify experiments/EXP-ECDLP-2b4ff1/runs/RUN-ECDLP-b883bf
```

Verify the two stored SHA-256 identities against the pointers/readback, decompress `modal-evidence-manifest.json.gz` to its logical JSON name, then extract the verified `modal-evidence.tar.gz` under this run directory (all members are regular files under `modal/`; enforce a safe data-only extraction). Re-run the existing transport check:

```sh
python3 harness/classical_ecdlp_endpoint_reuse/modal/admission_driver.py check --out experiments/EXP-ECDLP-2b4ff1/runs/RUN-ECDLP-b883bf
```

Independent public verification, the frozen analysis, unified export, plots and PDF are published separately under this experiment's `reports/run-20261027T1934Z/`. Every native clock remains `wall_valid=false`. Reported native counters have not received independent execution replay or execution-proof settlement.
