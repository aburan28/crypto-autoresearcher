#set page(paper: "a4", margin: (x: 1.6cm, y: 1.5cm), footer: context align(right, text(size: 8pt, counter(page).display("1"))))
#set text(font: "Liberation Sans", size: 9pt, lang: "en", ligatures: false)
#show raw: set text(font: "Liberation Mono")
#set par(justify: false, leading: 0.55em)
#set heading(numbering: none)
#show heading: set block(above: 0.8em, below: 0.4em)
#heading(level: 1)[#text("F7 second-pass preparation")]
#figure(image("diagram.svg", width: 100%, height: 5.4cm, fit: "contain"), caption: [Editable study diagram; exact scope and evidence paths appear in the report.])


#text("26 October 2026. Task TASK-20261026-59f4c9 is prepared for balanced genus-two arithmetic and norm checks. No second-pass arithmetic panel or pilot has run. Root must release the exact source, frozen protocol and real S3 gate before observation collection.")
#parbreak()

#text("The proposed panel constructs sixteen fixed rational C points and eight Frobenius-stable nonsplit degree-two supports, retaining every rejected draw. It executes sixteen rational add/subtract/double/cancel cases, eight nonsplit additions, eight associativity checks, and seven prior source pullbacks with balanced class addition. Principal-divisor, infinity-difference, corruption and missing-conjugate controls cover exceptions.")
#parbreak()

#text("The candidate implements full split-model balanced triples (u,v,n) with infinity counterweights. The actual reference reconstructs supports in Fp[i] and sums their elliptic images. The reference checks norms, and cannot prove class equality in the norm kernel. The nonzero infinity-difference class with zero norm is an explicit control against that invalid inference.")
#parbreak()

#text("See derivation.md for the balance convention and root-free norm, and literature.md for primary sources actually read. The existing Sage10.6 even-degree pair arithmetic is not used as an oracle. No plane-quartic Jacobian arithmetic, component-specific relation solver or advantage claim is supplied.")
#parbreak()

#text("Future commands, sequential with F5 in this worker, after root's release:")
#parbreak()

#text(size: 7.2pt)[#raw("python3 -B research/p256_factor_base_parallel_20261026/tracks/f7/run.py --out \nresearch/p256_factor_base_parallel_20261026/tracks/f7/runs/run-01 --seed 2026102607 --release \nresearch/p256_factor_base_parallel_20261026/runtime/releases/TASK-20261026-59f4c9.json\npython3 -B research/p256_factor_base_parallel_20261026/tracks/f7/export.py \nresearch/p256_factor_base_parallel_20261026/tracks/f7/runs/run-01 --out \nresearch/p256_factor_base_parallel_20261026/tracks/f7/export-run-01.json\npython3 tools/experiment_protocol.py check-export \nresearch/p256_factor_base_parallel_20261026/tracks/f7/export-run-01.json --protocol \nresearch/p256_factor_base_parallel_20261026/tracks/f7/protocol.json --verify-files", block: true)]

#text("Each fresh run directory retains raw cases, traces, checks, rows, identities, resource diagnostics and failures. Process clocks are diagnostic, with wall_valid=false. There is no observation export or result before execution; root will render and inspect the new report PDFs from actual recorded data.")
#parbreak()
