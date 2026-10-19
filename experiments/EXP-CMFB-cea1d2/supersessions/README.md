# CMFB run manifest schema completion

The eight original run manifests omit `run.result.certificate.kind`, which
produces eight ledger-validator errors. These hash-pinned replacements add
`kind: none` and a reason appropriate to the inventory, control, counting and
analysis measurements already recorded. No certificate is asserted.

The existing `tools/run_supersession_registry.yaml` routes schema validation to
these replacements and pins both sides. Each replacement points back to its
original manifest. The original run bytes, identifiers, code provenance,
results, decision, hypothesis, validation report and evidence remain unchanged.
This repair supplies no new execution, scientific approval, strength assignment
or research transition and adds no baseline exception.

The recorded analysis defects D1 and D2 and the separate superseding analysis
retain their existing status. Metadata completeness does not certify the
science, resolve procedure deviations or authorize future work.
