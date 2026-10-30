# Hexagon source intake and native integration pointers

The 2026-10-30 `cs.CC` snapshot contains 22 works, including cross-listings.
All 22 primary PDFs were retrieved and hashed. Their statements and relevant
limitations were reviewed; no full proof or Lean development was independently
rechecked. [knowledge-map.json](knowledge-map.json) maps every versioned work
to a new `KN-LIT` source note. A separate primary PKM construction review is
`KN-LIT-10b0fa`, superseding the abstract-only `KN-LIT-025` note.

The canonical source inventory, applicability catalog, code and detailed report
belong to `crypto:research/hexagon_cscc_20261030/`. The new native integrations
are divisor-prefix factoring, exhaustive weighted cost profiles, three
additional prime-field factory recipes and bounded counterexample controls.
All source claims remain reported; a retrieved proof claim or passing software
test does not promote an internal finding or an attack-cost bound.

For a sibling checkout, the source-constrained retrieval entry point is:

```sh
cargo run --locked --manifest-path ../crypto/tools/complexity-catalog/Cargo.toml -- --check
cargo run --locked --manifest-path ../crypto/tools/complexity-catalog/Cargo.toml -- locality
cargo run --locked --manifest-path ../crypto/tools/complexity-catalog/Cargo.toml -- certificate degree
```

Future research should read the returned assumptions, source/version and
implementation status. The catalog covers this dated collection only; no
recurring search, paid job or autonomous campaign was installed. No hypothesis,
goal, disposition, frontier or ledger status is changed by this intake. Existing
lead-atlas obstructions retain their tested scope; new compact encodings must
be evaluated on their actual sizes rather than inheriting a schoolbook-encoding
cost assertion without checking its premises.

## Validation and unresolved checks

The source-index unit suite and both generated-index checks are run for this
intake. `knowledge/INDEX.md` is generated and ignored under the current agent
contract; `knowledge/SOURCES.md` and `knowledge/sources.json` are tracked. The
existing artifact policy explicitly keeps `knowledge/sources.json` in Git.

The full `tools/validate_ledger.py` command refused this sparse checkout
because 140,590 tracked paths were initially off disk (140,589 after the
clean upstream fast-forward and artifact-tool hydration). Its bypass flag was not used and
the full-corpus check is not reported passed. This is a local validation limit,
not evidence against any paper. CI/full-checkout validation remains required.
Raw software-check output is retained in `checks/`.

[report.pdf](report.pdf) and [report.typ](report.typ) summarize this knowledge
intake. [catalog.json](catalog.json) and [integration.svg](integration.svg)
are byte-identical derived copies of the canonical crypto inputs. The shorter
local PDF stays below the existing artifact-policy data threshold; the full
seven-page source review is published with crypto. The shared performance/frontier graphs
were checked for affected claims; there are no new measurements or promoted
bounds, so their data and renderings do not change.

The remaining independent general tensor audit is recorded in
`crypto:problems/hashed-ecdl-tensor-backend.md`. Source-specific fast engines,
formal checks and qualified performance studies remain open obligations.
