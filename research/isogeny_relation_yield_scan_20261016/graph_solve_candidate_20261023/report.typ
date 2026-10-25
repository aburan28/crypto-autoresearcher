#set page(paper: "a4", margin: 20mm)
#set text(font: "Helvetica", size: 10pt)
= Candidate complete-solve path: bounded controls

2026-10-22. The current source was exercised on three public 19-point inputs
and one eight-target P37 prepared input. The two full-rank 19-point cases
recovered scalars 7 and 2; separate Sage point checks passed. The one-target
19-point input and the P37 input remained rank-censored.

#image("rank_summary.svg", width: 100%)

The P37 wrapper finished four independently checked phases under 8 GiB and
1,800 seconds. The solver saw rank 2 of 1,601 unknown columns. This tests
large-field parsing and matrix layout on eight public targets. It does not
establish full-quota rank, a completed P37 solve, an ECDLP time, or a rho
comparison. Commands, hashes, logs and resource receipts are retained in
the control directories and summarized in report.md.
