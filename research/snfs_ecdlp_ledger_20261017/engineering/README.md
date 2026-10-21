# Prospective manifest transport component

This is engineering preparation for the E3/D4 output-schema obligation. It runs no scientific producer and grants no execution authority. Seven fixture-only checks exercise current run-schema compatibility, source/identity/digest checks, preserved producer bytes, sealed-run refusal and no overwrite. The frozen producers, checkers and plans remain unchanged.

A future approved versioned driver would preserve the original producer manifest as `producer-manifest.yaml`, call `prepare` while a new run is still unsealed, and then let the ordinary supervisor run its checker, validate the schema and seal its own receipt. The component deliberately leaves `output_validated: false` and `scientific_review_verified: false`; it never fabricates a terminal supervisor outcome or attack certificate.

No scientific trial was run to test this component. Fixture parameters and raw values are explicitly labeled as synthetic fixtures. Passing schema checks is neither execution proof nor mathematical validation. The component does not fix preapproval routing, source binding, lane ownership or the lawful approval obligations recorded in the [repair packet](../../../coordination/design/SNFS-INSTRUMENT-REPAIR-20261017/README.txt). Those remain prerequisites before use in a scientific run.

Run fixture checks from the repository root:

```sh
python3 research/snfs_ecdlp_ledger_20261017/engineering/test_manifest_transport.py
```
