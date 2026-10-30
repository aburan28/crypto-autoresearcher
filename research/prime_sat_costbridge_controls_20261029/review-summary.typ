#set page(paper: "a4", margin: (x: 16mm, y: 14mm), numbering: "1")
#set text(font: "DejaVu Sans", size: 9.2pt)
#set par(justify: false, leading: 0.45em)
#set heading(numbering: none)
#text(size: 19pt, weight: "bold")[Checker controls now have independent execution evidence]

#text(fill: rgb("#235a3a"), weight: "bold")[DEC-20261029-76b793 · scoped archival acceptance]

All *six review joints hold*. The independent reviewer executed *seven fixed families and 250 passing named assertions*, then the exact original *18-test regression suite*: two return-zero invocations, no repair or repeat. Producer execution separately passed seven families and the same 18 regressions. These are related fixed software checks, not scientific samples or performance measurements.

This adds evidence to the prior source audit. *DEC-266f95 keeps its historical independent-execution-inconclusive finding.* Original code, tests, receipts and scientific statuses remain unchanged. Archival effect requires the native ten-path ledger binding.

#table(columns: (1.1fr,3.3fr), inset: 4pt, stroke: 0.4pt + rgb("#c5d1db"),
 table.header([*Joint: holds*],[*Actual fixed observation*]),
 [False nonroot],[At p=5, empty D2 preserves the empty projected set and correct digest. Original checker rejects the false row at exactly the nonroot-certificate guard. Suppressing only that guard in memory admits the same bad artifact; the mutant certifies nothing.],
 [Rehashed inputs],[Duplicate domain, singular curve, off-curve target and zero-ordinate target fail their four named guards despite correct recomputed digests. Producer solve rejects all four too.],
 [On-curve sums],[Both mutations retain domains, projections, digest and on-curve points. The checker separately rejects wrong sum abscissa and same-abscissa wrong ordinate; independent addition confirms the latter sums to −R.],
 [Exceptions / roots],[At p=7, the order-three target retains projection (0,0) with (−R,−R); deletion fails completeness. At p=17, the independent tiny oracle agrees, v₂(p−1)=4, Z=3 and the two setup probes are checked.],
 [Prefix coverage],[Nine covers/gaps and eleven invalid-input cases pass. Three n=256 fixtures use no cube enumeration. Returned gaps are independently checked against the domain and every prefix.],
 [Execution custody],[Both independent commands ran. All frozen before/after/current hashes, command/stream digests and embedded harness bytes match. The unchanged native independence gate passed.],
)

#v(3pt)
#image("review-summary.svg", width: 100%)
#text(size: 7.7pt)[Fixed source/receipt observations only; no benchmark axes, samples or uncertainty estimates. Exact identities and commands: review-inputs.json. Targets: prefix_cover.py and unchanged reference.py/check_reference.py; independent harness and receipt: TASK-20261029-3c8d06/.]

#pagebreak()
#text(size: 16pt, weight: "bold")[What the utility establishes, and what remains separate]

A pair (d,k) covers n-bit assignments whose *lowest d bits* equal k; variable 0 is first. Optional auxiliary range is bits >> m < bound. Terminal trie nodes cover subtrees. A missing valid child returns a concrete zero-filled gap; subtrees whose minimum auxiliary value is already out of range are pruned. The iterative implementation has no full-cube scan.

The n=256 two-half cover, one-half hole and empty-prefix cover allocate *3, 2 and 1 nodes*. The one-half gap is *1*. The auxiliary boundary cover has 13 nodes; its hole has 12 nodes and gap 5. Empty/duplicate/overlapping prefixes, empty auxiliary domains and a censored cover are tested explicitly. These counts describe the fixed fixtures only.

Source accounting is at most *1 + Σ depth* allocated nodes and *O(number of prefixes + Σ depth)* input/trie operations, plus integer-bit, input and output costs. Zero-depth entries still require validation; an exponentially long transcript remains expensive. Fixed tests and source inspection are not a formal all-input complexity proof.

Every result retains *arithmetic_verified=false*. Boolean coverage checks no polynomial refutation, curve model or projected fiber. A returned gap need not be an arithmetic solution. No transcript adapter or arithmetic SAT/UNSAT certificate is accepted here. Four input cases isolate four guards; p=17 covers one high 2-adic valuation, not every Tonelli–Shanks branch. Mathematical primality remains a premise. Probe/node fields and clock stamps are narrow software/custody facts, not total work or timing evidence.

#text(weight: "bold")[Independent review and custody.]
One separate reviewer authored assertions without reading the producer’s new tests, results or README; reading/importing the frozen targets was allowed. This is independent software testing, not blind theorem derivation. Epoch 1 failed at a provider usage limit before any output or suite. That failed release is retained. The same blinded actor resumed at epoch 2 after permitted administrative identity/ownership messages. Requested native Codex gpt-6.1-sol/xhigh/fork-none is not authenticated serving-model evidence; model/effort and opaque UUID remain unknown.

The unchanged native checker returned zero at *2026-10-30 00:51:34 UTC*. Coordinator recomputed the four review hashes, checker hash, argv/stdout/stderr digests, embedded harness identity and all frozen source hashes. The manifest embeds the exact parsed native receipt and its original-file SHA256, without asserting identical JSON serialization. Synthesis ran no additional software suite or solver.

Producer `47c25f284d` is bound by five-path snapshot `dc4d2997af67`. Review source `6edcddc5ae`, completed release `f020b956bb` and ledger epoch-1 claim `a513bd23b5` establish the present custody. Prior PR2679 merged; branch is `codex/prime-sat-controls-review-20261030`. Root found no scoped changes from `c98828b779` to fresh main `bd4288fa68`. The earlier reconciliation’s null execution field predates the sealed receipt.

Full ledger validation refused *155,566 off-disk tracked paths*; no bypass. Root reports scoped pre-change hygiene and the pre-PDF artifact-store check passed, not full-ledger/final-head approval. Prior artifact uploads and remote readbacks succeeded. The separate checkpoint helper earlier selected no admitted credential transport despite ambient AWS CLI access. A configured-provider export is available, but the new checkpoint bridge is *not uploaded at synthesis*. Root records actual later rendering/storage/checkpoint outcomes in the manifest and binds the ten-path archive.

#text(weight: "bold")[Next concrete integration candidate.]
Separately admit an adapter for the existing LSB-prefix transcript, independently validating each algebraic refutation, model/projection fiber and auxiliary domain before coverage supports completeness. Future arbitrary-literal partial-trail clauses require a different proof/completeness interface or an explicit prefix restriction with conversion cost charged. This utility does not establish that integration or a solver gain.

No formal proof, novelty, solving-degree gain, measured speedup, scalar recovery or general ECDLP advantage follows. GOAL-PFDR-fd09e0 remains active; no H/EV/KN or goal transition. Historical PNEXT invalid_output stays unchanged. The three prior regularity diagrams and prior cost-bridge diagram were inspected and preserved as historical scopes; this diagram adds fixed software observations without changing canonical scientific relationships.
