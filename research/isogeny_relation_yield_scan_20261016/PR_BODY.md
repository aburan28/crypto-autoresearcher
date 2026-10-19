## Scope

Archives the prespecified degree-7 isogeny graph needed for the larger relation-yield study: 2,048 P29 edges and 256 P37 edges, with 2,306 distinct vertices in total. The two complete JSONL streams, the interrupted first P29 prefix, producer source, independent verifier, protocol draft, amendment, content manifest, graph, and inspected PDF are self-contained under one directory.

## Checks

- The producer checked each rational degree-7 map, codomain order, dual identity on the transported generator and smoke target, canonical model, and scalar transport.
- An independent pure-Python checker passed on all 2,304 full-path edges. It checked continuity and unique `j`, recomputed `j`, proved that the saved cubic kernel divides the seventh division polynomial, recomputed the Vélu codomain, and replayed transported point arithmetic.
- `manifest-v2.json` content hashes match all 16 listed files. The PDF compiles as one page and was visually inspected.

## Limits and next stage

The checker does not independently reconstruct the full point-map formula or dual. Relation yield, useful rank, and end-to-end ECDLP cost have not yet been measured on these vertices. The protocol remains a draft pending a runnable collector and Coordinator approval. The amendment applies the owner's current progress rule: compare complete cost `S` against the best verified frozen index-calculus baseline for the same curve and size, while reporting the remaining gaps to matched rho and the setup-excluded Bernstein–Lange reference.

The earlier P29 attempt was interrupted after 569 edges; its raw prefix remains in the archive. Sage initially failed before opening the P37 output because its cache path was denied by the sandbox; the bounded rerun used a cache inside the claimed directory. The manifest records missing subprocess logs and peak RSS for these preparatory walks.
