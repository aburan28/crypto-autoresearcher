#set page(paper: "a4", margin: 17mm)
#set text(size: 9pt)
#set heading(numbering: none)

= Planted satisfiable XCNF controls for k11 binary bases

*Exact constructed-model input preparation, 2026-10-17 UTC.* One synthetic
known-point target was built separately for each of the frozen 316-column
weighted and local-random bases on the certified GF(2^61) ordinary-binary
curve. Their complete Boolean assignments satisfy every serialized CNF clause
and native XOR row. No SAT solver or natural relation trial was run.

#image("2026-10-17-binary-k11-planted-xcnf.svg", width: 100%)

The weighted and local-random formulas have 88,930 and 88,842 variables,
89,122 CNF clauses each, and 62,687 and 62,599 native XOR rows. Both have
11,328 exact-membership exclusion clauses. These counts describe inputs,
not observed solver work or degree of regularity. The complete manifest
SHA-256 is `922c1c727fe8635355042f726ef5bf5335a26bd00d930b17fe23c528812c11b3`.

== Evidence and next gate

The independent checker re-parsed both full models and every XCNF constraint,
and bound the earlier Sage group replay of the two synthetic point sums.
The first generator attempt wrote the weighted inputs then failed on a
relative-path conversion; those exact files and its source hash are retained.

A Coordinator-approved bounded solver protocol can now test CryptoMiniSat on
both SAT-positive controls, then on the four archived channels with exact
point certificates. The archived target derives from an earlier base, so a
new base-independent schedule is required for a factor-base yield comparison.
Full end-to-end work still needs certified natural relation yield, useful rank,
linear algebra, unseen same-point target cost, complete setup and matched rho.
Solver-reported UNSAT would remain unvalidated without a proof; SAT alone
does not measure algebraic degree of regularity.

The companion Markdown report links all immutable files. The canonical
ECDLP frontier graph was checked and requires no update from this input work.
