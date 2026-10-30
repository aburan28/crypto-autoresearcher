#set page(paper: "a4", margin: (x: 1.6cm, y: 1.5cm), footer: context align(right, text(size: 8pt, counter(page).display("1"))))
#set text(font: "Liberation Sans", size: 9pt, lang: "en", ligatures: false)
#show raw: set text(font: "Liberation Mono")
#set par(justify: false, leading: 0.55em)
#set heading(numbering: none)
#show heading: set block(above: 0.8em, below: 0.4em)
#heading(level: 1)[#text("F5 second-pass preparation")]
#figure(image("diagram.svg", width: 100%, height: 5.4cm, fit: "contain"), caption: [Editable study diagram; exact scope and evidence paths appear in the report.])


#text("26 October 2026. Task TASK-20261026-26de77 is prepared for a frozen exact panel. No second-pass arithmetic panel or pilot has run. Experimental execution awaits root's exact Phase B release, the committed frozen protocol and the successful real S3 checkpoint gate.")
#parbreak()

#text("The proposed panel uses all four prior P-256 maps (degrees 3,5,11,11), eight canonical source points, sixteen signed labels and six targets. Three targets are constructed correctness controls, two use a fixed hash-to-point law, and one is O. Each complete source relation set is compared with the same labelled endpoint set. Membership, inverse transport, geometric pole certificates and a coordinate-isomorphism control are retained separately.")
#parbreak()

#text("Two actual algorithms are exported: the exhaustive affine source oracle and the endpoint/Jacobian pair lookup. Their shared setup and unequal work scopes preclude a method-cost comparison. No natural yield or scaling inference is planned. See derivation.md, literature.md, protocol.draft.json and the root-owned execution gates for exact assumptions and controls.")
#parbreak()

#text("Future commands, from the repository root, after root releases the exact source/protocol/checkpoint identities:")
#parbreak()

#text(size: 7.2pt)[#raw("python3 -B research/p256_factor_base_parallel_20261026/tracks/f5/run.py --out \nresearch/p256_factor_base_parallel_20261026/tracks/f5/runs/run-01 --seed 2026102605 --release \nresearch/p256_factor_base_parallel_20261026/runtime/releases/TASK-20261026-26de77.json\npython3 -B research/p256_factor_base_parallel_20261026/tracks/f5/export.py \nresearch/p256_factor_base_parallel_20261026/tracks/f5/runs/run-01 --out \nresearch/p256_factor_base_parallel_20261026/tracks/f5/export-run-01.json\npython3 tools/experiment_protocol.py check-export \nresearch/p256_factor_base_parallel_20261026/tracks/f5/export-run-01.json --protocol \nresearch/p256_factor_base_parallel_20261026/tracks/f5/protocol.json --verify-files", block: true)]

#text("The proposed data will support fixed-domain exactness observations only. All failure paths retain their output directory. No result, flow or current PDF is fabricated before data. Root owns final report rendering and the PR.")
#parbreak()
