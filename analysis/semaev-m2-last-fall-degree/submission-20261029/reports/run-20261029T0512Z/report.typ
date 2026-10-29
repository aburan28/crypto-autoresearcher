#set page(paper: "a4", margin: 17mm)
#set text(size: 10pt)
#set par(justify: false)
= Semaev certificate data: progress snapshot
2026-10-29T05:12:18.930672+00:00

This report records observations from an incomplete campaign. It makes no scientific promotion, asymptotic, population-frequency, or performance claim. Missing results remain missing.

Historical replay: *13 of 13 certificates independently accepted*, each with its previously recorded SHA-256. Public certificate downloads with complete hash readback: *16*. Fresh solution counts completed: *8 of 190*.

#table(columns: (1fr, 0.5fr, 2fr, 1fr), inset: 5pt,
"Instance",
"n",
"Observed status",
"codim bound",
"C19a",
"19",
"certificate_verified",
"9253",
"C19b",
"19",
"certificate_verified",
"6817",
"P45a",
"45",
"certificate_verified",
"12742",
"Q35a",
"35",
"certificate_verified",
"5287",
"Q35b",
"35",
"certificate_verified",
"5287",
"R35a",
"35",
"certificate_verified",
"5287",
"R35b",
"35",
"certificate_verified",
"5287",
"R37a",
"37",
"certificate_verified",
"10066",
"R37b",
"37",
"certificate_verified",
"10066",
"T33a",
"33",
"certificate_verified",
"4888",
"T33b",
"33",
"certificate_verified",
"4888",
"U35a",
"35",
"certificate_verified",
"5287",
"U35b",
"35",
"certificate_verified",
"5287")

#image("historical-certificates.svg", width: 100%)

The independent checker proves that the bounded-degree closure is contained in the kernel of the supplied map. Its codimension is therefore at least the plotted value. Equality is not claimed. Historical solution counts are carried in the original input records and were not recomputed by this replay.

Source: the exact named replay records under `evidence/replay/`, their certificate digests, and public readback acknowledgements in `publication-index.json`. The displayed dimensions are exact checked lower bounds; no uncertainty interval or averaging applies.

#pagebreak()
= Prospective panel and remaining data
The frozen plan has 190 exact input presentations: ten per integer n from 33 to 45 and from 47 to 51, plus ten separately labelled trace-zero inputs at n=33. Ordinary strata have five polynomial and five random subspaces. Every draw is retained, including easy refutations and solvable inputs.

There are 190 degree-four closure requests and 50 additional degree-five requests on the frontier inputs. Degree-five closure is required to certify a lower bound of six. A prospective memory refusal remains unknown; it is not a degree-five ceiling.

#image("coverage.svg", width: 100%)

Fresh lower bounds require both an accepted certificate and an exact exhaustive solution count smaller than the checked codimension. Neither the 190 generated parameter records nor a producer's solver trace substitutes for that conjunction. The graph shows progress counts only.

Execution: two closure workers, each with a 40 GiB address-space ceiling and a six-hour command watchdog. The host is shared, so all wall-valid flags are false. Completed instance records are restartable; in-progress elimination has no process checkpoint. Source and binary hashes are pinned in the copied protocols. Active-run recovery details live in the S3 resume checkpoint.

Software controls: the native counter passed 188 small full enumerations and four batch-boundary comparisons with another counting algorithm. Four damaged-certificate copies were rejected by the independent checker. These are software checks, not a formal proof of the counter.

Known limitations: the separate pre-run S3 checkpoint gate was missed and corrected after launch. The generic unified export mapping remains incomplete. Human expert review is deferred by the owner. None of these is hidden by the certificate or software-check results.
