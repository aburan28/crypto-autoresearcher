#set page(paper: "us-letter", margin: 0.7in)
#set text(font: "Libertinus Serif", size: 10pt)

= AUXIN successor draft classification

Mechanical validation, 2026-10-28. The placed `EXP-AUXIN-339fb0/specification.yaml` is a draft successor contract, not an approved executable experiment. Its bytes match the design-stage `draft-contract.yaml`; both have SHA-256 `6a1dca32c109d5badf4ba143c31f9d4d9a49e18ae287c8bb4fc604526bf02ecc`. Both declare draft status and null approval fields.

#image("classification.svg", width: 100%)

The validator accepts only the exact path, both exact source hashes, and matching draft/identity fields. It emits an advisory, keeps reference resolution to the placed draft, and does not register an experiment ID. Changed status, approver, identity, source bytes, or path cannot take the draft route. A changed source retains the ordinary schema error.

Three targeted unit tests passed. The archived files, suppression baseline, numerical results, and performance graphs are unchanged. The earlier full-ledger job had 65 unsuppressed errors; removal of this one line is expected but must be confirmed by the complete-tree hosted run. This report does not claim a clean ledger gate or scientific validation.
