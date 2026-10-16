#set page(paper: "a4", margin: 22mm)
#set text(size: 10pt)
#set heading(numbering: "1.")

= Degree-7 isogeny walk search: verified graph, pending relation study

#emph[Research record, 16 October 2026.] This report covers graph enumeration
only. The two requested finite paths contain 2,304 directed degree-7 edges
and 2,306 distinct vertices. Three-summand relation yield, useful rank and
end-to-end ECDLP time have not yet been measured on these paths.

#image("graph.svg", width: 100%)

== Inputs and fixed search

The source curves are the P29 and P37 floor curves named in the ECTD study.
The prospective design chose 2,048 P29 and 256 P37 directed edges before
enumeration. At every step, the producer required two rational degree-7
neighbors, selected the nonbacktracking neighbor, and stopped on repeated
`j`. It transported a generator and a smoke target through each map and
checked the dual identity at every edge. The code and raw JSONL are in the
linked study directories; the continuation used the same producer on a new
write-once output path.

== Observations and independent checks

Both full paths ended with a completion record. The P29 path has 2,048
edges and 2,049 distinct `j` values; P37 has 256 edges and 257 distinct
`j` values. The independent checker parsed every edge, checked continuity
and unique `j`, recomputed each curve's `j`, proved that the saved cubic
kernel divides the seventh division polynomial, recomputed the raw Vélu
codomain, and verified the saved generator and smoke target with separate
point arithmetic. Both full verification reports passed. The checker does
not rederive the complete isogeny point formula; the Sage producer's map
and dual checks are a second, implementation-dependent layer.

An earlier P29 attempt stopped after 569 saved edges when the chat session
was interrupted. Its prefix and raw file remain unchanged, and the same
independent checks pass on those 569 edges. It is an interrupted attempt,
not a mathematical counterexample or a yield result.

== Decision boundary

These finite graph results make 2,306 curve presentations available for
the prespecified base and target experiment. They do not rank any curve by
relation yield or ECDLP cost. The next stage requires a frozen runnable
collector, seed commitments, the full base/target controls, and Coordinator
approval. A verified improvement compares complete cost `S` against the
best frozen index-calculus pipeline for the same curve and size; matched rho
and the setup-excluded Bernstein–Lange reference remain reported distances.
The protocol amendment is in `AMENDMENT.md`.

== Evidence files

`walk-p29-2048-attempt2.jsonl`, `walk-p37-256.jsonl`,
`verification-p29-full.json`, `verification-p37-full.json`,
`verify_walk.py`, and `manifest-v2.json` bind this report. The producer,
planning draft and interrupted prefix are copied into this continuation so
the committed evidence remains self-contained. The first manifest is retained
as a superseded draft because it pointed to uncommitted adjacent files.
