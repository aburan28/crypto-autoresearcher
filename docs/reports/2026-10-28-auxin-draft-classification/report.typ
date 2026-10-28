#set page(paper: "us-letter", margin: 0.7in)
#set text(font: "Libertinus Serif", size: 10pt)

= AUXIN successor draft classification

Mechanical validation, 2026-10-28. The placed `EXP-AUXIN-339fb0/specification.yaml` is a draft successor contract, not an approved executable experiment. Its bytes match the design-stage `draft-contract.yaml`; both have SHA-256 `6a1dca32c109d5badf4ba143c31f9d4d9a49e18ae287c8bb4fc604526bf02ecc`. Both declare draft status and null approval fields.

#image("classification.svg", width: 100%)

The validator accepts only the exact path, both exact source hashes, and matching draft/identity fields. It emits an advisory, keeps reference resolution to the placed draft, and does not register an experiment ID. Changed status, approver, identity, source bytes, or path cannot take the draft route. A changed source retains the ordinary schema error.

Eleven targeted and adjacent unit tests passed. The complete-tree hosted job on head `07460029...` compared with main `fb55b843...`: 65 errors in 22 paths became 64 in 21, with exactly the AUXIN top-level-key error removed and zero added. Advisories rose from 578 to 579. Both full validators still exit 1; the relative CI gate passes. The archived files, suppression baseline, numerical results, and performance graphs are unchanged. This report does not claim a clean ledger gate or scientific validation.
