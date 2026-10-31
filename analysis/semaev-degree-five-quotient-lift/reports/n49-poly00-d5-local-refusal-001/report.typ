#set page(paper: "a4", margin: 18mm)
#set text(size: 10pt, font: "Libertinus Serif")
= n49 poly00 v1 local preflight refusal
Host admission passed on sample 11 after 110.266 seconds, with 37,462,147,072 available bytes. The worker then refused the request because `disk_policy.N=49` was the curve parameter, while the published seed has *50 Boolean variables* (`2k`, with `k=25`). No seed transfer, checker, exact count or D5 producer ran.

#image("flow.svg", width: 100%)

The raw refusal record is `runs/n49-poly00-d5-local-preflight-refusal-001/manifest.json`. The frozen v1 protocol remains unchanged. A separate v2 request corrects `N=50`, uses a fresh output root, and adds pre-admission dimension checks. This operational refusal gives no LFD conclusion.
