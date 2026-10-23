#set page(margin: 1.7cm)
#set text(size: 10pt)
= The recovered 17 November 1997 X9.62 draft
<the-recovered-17-november-1997-x9.62-draft>
#strong[Date:] 2026-10-23 UTC. #strong[Question:] Does the original
November 1997 working draft contain a rule that rejects the eleven
otherwise qualifying seed candidates? #strong[Result:] We recovered the
full 103-page draft. Its stated prime-field curve-generation procedure
gives no additional candidate predicate separating those eleven from the
published curves. It already prints the seven published 192-, 239-, and
256-bit prime curves, including P-256. The actual generator's decision
trace is still missing.

== Primary source and exact provenance
<primary-source-and-exact-provenance>
The
#link("https://archive.org/details/x962-11-17-97")[Internet Archive item]
hosts a
#link("https://archive.org/download/x962-11-17-97/x962-11-17-97.pdf")[PDF of the ANSI X9.62 working draft].
Its cover is dated #strong[17 November 1997] (PDF page 1). The
591,731-byte, 103-page PDF has SHA-256
`0c231d5176fcf0b239b44732213d281b518a0e16cc6f13f7bd4039ec99807b6e`. Its
PDF metadata says Acrobat Distiller 3.01 created the file on 11 December
1997; the archive item says it was uploaded in 2017. Metadata and
archive upload do not independently notarize when every page first
circulated. The cover, procedure, and P-256 table page were visually
inspected. #link("source_check.json") binds the source hash, exact
sample seeds, page locations, and prior check record.

The table in §H.5, PDF pages 97--101 (printed pages 89--93), explicitly
calls the prime-field entries #emph[sample curves] for implementation
checking. It contains P-192, prime192v2, prime192v3, prime239v1,
prime239v2, prime239v3, and P-256. The seven 160-bit seeds in that table
match the named published seeds exactly, verified by
#link("verify_source.py") against the PDF text. In particular, PDF page
100 (printed page 92) gives P-256's `C49D3608...` seed and `5AC635D8...`
coefficient. This places those seven published parameter sets in a dated
#strong[November/December 1997 artifact], much earlier than the
September 1998 cover of the later draft. It does not say when the May
and August generation runs ended or how competing candidates were
evaluated.

== What the draft says to accept
<what-the-draft-says-to-accept>
Section F.3.2, PDF page 63 (printed page 55), specifies: choose a seed
and derive a curve, count its order, check nonsingularity, test
near-primality of the order, check MOV and anomalous conditions, find a
prime-order point, and output the curve. The note on PDF page 64
requires the order lower bound to exceed `2^160` and says the
trial-division limit is typically 255. Section F.2.2, PDF page 62,
defines near-primality through a smooth cofactor and a probably prime
large factor. Section F.3.3, PDF page 64, starts by choosing an
arbitrary seed bit string at least 160 bits long. The visible text gives
#strong[no schedule for the next seed after a candidate is rejected or
passed] and no rule for selecting one of several passing curves for the
published examples.

The existing
#link("../nist_seed_selection_workflow_20261023/check.json")[exact 21-row workflow comparison]
records eleven omitted and ten published classes satisfying the named
cofactor-one, `n>2^160`, nonanomalous, and stronger-than-required
`MOV B=100` checks. #link("verify_source.py") hashes and checks that
prior matrix; it does not rerun its arithmetic. Since every omitted
curve has prime full order, its cofactor is 1 and its near-primality
check succeeds for any ordinary trial-division bound. Thus the
#strong[stated November 1997 procedure] does not explain passing over
the eleven. A local software error, unpublished policy, different input
or state, or later review remains possible. The stipulation that the
historical program actually evaluated and rejected all eleven remains a
hypothesis.

#figure(image("selection_gap.svg", alt: "Draft procedure and unresolved decision"),
  caption: [
    Draft procedure and unresolved decision
  ]
)

== What changed, and what would settle the question
<what-changed-and-what-would-settle-the-question>
The missing November draft is now acquired. Its parameter appendix
establishes that the seven published examples were fixed in this
available artifact by its stated date and PDF creation timestamp. The
earlier #strong[21 June 1996], #strong[15 January 1997], and #strong[11
June 1997] drafts cited by independent sources remain acquisition
targets, especially for how the procedure changed before and during the
May seed runs. The original program, its run log, and candidate-level
review notes would be stronger evidence for the actual keep/skip
decisions.

An independently specified weakness predicate must still classify all
eleven omissions and matched published controls, including P-256 blocks
876 and 1842, and yield a checkable attack mechanism or historical
decision record. The recovered draft supplies neither. Its dated table
strengthens provenance and rules out an extra #strong[documented]
November 1997 acceptance gate; it does not identify the postulated
common weakness. The
#link("../../problems/nist-seed-selection-rule-unexplained.md")[open selection problem]
remains open. No ECDLP cost claim or official research-status transition
follows.

== Reproduction
<reproduction>
Download the PDF from the source link and run
`python3 research/nist_seed_1997_original_draft_20261023/verify_source.py --pdf /path/to/x962-11-17-97.pdf --output /tmp/source_check.json`.
The script requires the exact SHA-256 and seven table seeds, and
validates the previously archived gate matrix's identity and true
predicates. The supplied source PDF is linked and hash-bound, not
redistributed. The report, editable diagram, SVG and visually inspected
PDF record this substantive source search. Source statements are
`retrieved`\; matched-curve screening is `internal` and `derived`\;
historical intent and execution are unobserved.
