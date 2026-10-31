#set page(paper: "a4", margin: 22mm)
#set text(size: 10pt)
= Export admission guard controls
Observations only. All 20 actual local software controls passed, ten fresh and ten restored. This rendering supplements the immutable export-guard-001 report; no trial was rerun.

Allowed exports match the retained reference certificate. Fresh refusal preserves a published, verified checkpoint; restored refusal prevents native execution. Exact-capacity and one-byte-short cases use the common prelaunch path in both configurations. Corrupt state, mismatched identity, and existing output paths are rejected.

#image("../export-guard-001/outcomes.svg", width: 100%)

All 169 archived files were verified against sizes and SHA-256 hashes. The twenty-row experiment export validates with zero findings. Source report: export-guard-001/report.md. Protocol SHA: d8686cd06e99f7b4d73efc099673e767ea3a4cb4dd4b4cbef3e7c7beade9805e.

These are local fake-storage controls. No cloud resource qualification, performance result, or new LFD bound follows. Worker integration remains required.
